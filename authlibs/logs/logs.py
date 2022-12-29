# vim:shiftwidth=2:expandtab

from ..templateCommon import  *

from datetime import datetime
from .. import accesslib
from .. import ago
import subprocess
import glob

# ------------------------------------------------------------
# API Routes - Stable, versioned URIs for outside integrations
# Version 1:
# /api/v1/
#        /members -  List of all memberids, supports filtering and output formats
# ----------------------------------------------------------------

# You must call this modules "register_pages" with main app's "create_rotues"
blueprint = Blueprint("logs", __name__, template_folder='templates', static_folder="static",url_prefix="/logs")

# --------------------------------------
# Routes
#  /test : Show (HTTP GET - members()), Create new (HTTP POST - member_add())
#  /test/<id> - Some ID
# --------------------------------------

# ------------------------------------------------------------
# Logs  
#
# Things log like crazy. Therefore logs are designed to
# be cheap to write, and to be compartimentalizable so
# that they don't interfere with other stuff.
#
# So we put logs in a separate databse. Maybe someday this
# could be a completely different type of datastore.
#
# Because of this, we can't do relational queries between
# the log and main databases. 
#
# Because of all this, logs are expensive to read. This might
# not be too bad because we don't read them all that often.
# ------------------------------------------------------------

@blueprint.route('/', methods=['GET'])
@login_required
def logs():
    eastern = dateutil.tz.gettz('US/Eastern')
    utc = dateutil.tz.gettz('UTC')
    now = datetime.now()
    limit = 200
    offset = 0
    format='html'
    evt= eventtypes.get_events()
    # Query main DB to Build relational tables
    tools={}
    members={}
    resources={}
    nodes={}
    for t in Tool.query.all():
            tools[t.id] = t.name
    for r in Resource.query.all():
            resources[r.id] = r.name
    for n in Node.query.all():
            nodes[n.id] = n.name
    for m in Member.query.all():
            members[m.id] = {
                    'member': m.member,
                    'first': m.firstname,
                    'last': m.lastname,
                    'email': m.email
                    }

    # Start Query
    # We will do TWO queries that are almost identical - a normal one, 
    # and a "count" with the limit (and offset) disabled
    for qt in ('normal','count'):
        q = db.session.query(Logs).order_by(Logs.time_reported.desc())

        # Resource Filter
        filter_group = list()
        for x in request.values:
                if x.startswith("input_resource_"):
                        filter_group.append((Logs.resource_id == x.replace("input_resource_","")))
        if (len(filter_group)>=1):
                q = q.filter(or_(*filter_group))
                        
        # Member Filter
        filter_group = list()
        for x in request.values:
                if x.startswith("input_member_"):
                        filter_group.append((Logs.member_id == x.replace("input_member_","")))
        if (len(filter_group)>=1):
                q = q.filter(or_(*filter_group))

        # Tool Filter
        filter_group = list()
        for x in request.values:
                if x.startswith("input_tool_"):
                        filter_group.append((Logs.tool_id == x.replace("input_tool_","")))
        if (len(filter_group)>=1):
                q = q.filter(or_(*filter_group))

        # Node Filter
        filter_group = list()
        for x in request.values:
                if x.startswith("input_node_"):
                        filter_group.append((Logs.node_id == x.replace("input_node_","")))
        if (len(filter_group)>=1):
                q = q.filter(or_(*filter_group))

        if 'input_date_start' in request.values and request.values['input_date_start'] != "":
            dt = datetime.datetime.strptime(request.values['input_date_start'],"%m/%d/%Y")
            q = q.filter(Logs.time_reported >= dt)
        if 'input_date_end' in request.values and request.values['input_date_end'] != "":
            dt = datetime.datetime.strptime(request.values['input_date_end'],"%m/%d/%Y")+datetime.timedelta(days=1)
            q = q.filter(Logs.time_reported < dt)


        # Let's add additional filters, depending on who's asking...
        if current_user.privs('Useredit','Finance','RATT'):
          # Global Privs which can see everything - no additional filtering
          pass
        elif accesslib.user_is_authorizor(current_user,level=AccessByMember.LEVEL_ARM):
          # User is an ARM on at least one resource - let them see stuff pertianing to those resources,
          # their related tools, and the nodes they run on
          # TODO

          # Find resources I manage
          myres = AccessByMember.query.join(Resource,((Resource.id == AccessByMember.resource_id) & (AccessByMember.level >= AccessByMember.LEVEL_ARM)))
          myres = myres.filter(AccessByMember.member_id == current_user.id)
          myres = myres.add_columns(Resource.id,Resource.name).all()
          #print "START",len(myres)
          my_resources=[]
          for x in myres:
              my_resources.append(x.id)

          # Find Tools in these resource groups
          my_tools=[]
          my_nodes=[]
          ndlist={}
          tls = Tool.query.filter(Tool.resource_id.in_(my_resources)).all()
          for t in tls:
            my_tools.append(t.id)
            ndlist[t.node_id] = 1

          for n in ndlist.keys(): my_nodes.append(n)

          # I can see my own records (but not comments), too
          my_filter = and_(Logs.member_id.__eq__(current_user.id), Logs.event_type.__ne__(eventtypes.RATTBE_LOGEVENT_COMMENT.id))
          filter_group = (Logs.node_id.in_(my_nodes),Logs.resource_id.in_(my_resources),Logs.tool_id.in_(my_tools),my_filter)
          q = q.filter(or_(*filter_group))
        else:
          # This is a "normal" unprivileged user. They can only see their own records (excluding comments)
          q = q.filter(Logs.member_id == current_user.id)
          q = q.filter(Logs.event_type != eventtypes.RATTBE_LOGEVENT_COMMENT.id)

        # Normal query format


        if ('member' in request.values):
                        q=q.filter((Logs.member_id==members[request.values['member']]) | (Logs.doneby==members[request.values['member']]))
        if ('memberid' in request.values):
                        q=q.filter((Logs.member_id==request.values['memberid']) | (Logs.doneby==request.values['memberid']))
        if ('resource' in request.values):
                        q=q.filter(Logs.resource_id==resources[request.values['resource']])
        if ('resourceid' in request.values):
                        q=q.filter(Logs.resource_id==request.values['resourceid'])
        if ('tool' in request.values):
                        q=q.filter(Logs.tool_id==tools[request.values['tool']])
        if ('toolid' in request.values):
                        q=q.filter(Logs.tool_id==request.values['toolid'])
        if ('before' in request.values):
                        q=q.filter(Logs.time_reported<=request.values['before'])
        if ('after' in request.values):
                        q=q.filter(Logs.time_reported>=request.values['after'])
        if ('format' in request.values):
                        format=request.values['format']

        # TODO - eventually allow a way to show active/inactive messages
        if ('activity' not in request.values):
          q=q.filter(Logs.event_type!=eventtypes.RATTBE_LOGEVENT_TOOL_ACTIVE.id)
          q=q.filter(Logs.event_type!=eventtypes.RATTBE_LOGEVENT_TOOL_INACTIVE.id)

        if ('hidetoolusage' in request.values):
          q=q.filter(Logs.event_type!=eventtypes.RATTBE_LOGEVENT_TOOL_POWEROFF.id)
          q=q.filter(Logs.event_type!=eventtypes.RATTBE_LOGEVENT_TOOL_POWERON.id)
          q=q.filter(Logs.event_type!=eventtypes.RATTBE_LOGEVENT_TOOL_LOGIN.id)
          q=q.filter(Logs.event_type!=eventtypes.RATTBE_LOGEVENT_TOOL_LOGOUT.id)
          q=q.filter(Logs.event_type!=eventtypes.RATTBE_LOGEVENT_TOOL_LOGIN_COMBO.id)
          q=q.filter(Logs.event_type!=eventtypes.RATTBE_LOGEVENT_TOOL_PROHIBITED.id)
          q=q.filter(Logs.event_type!=eventtypes.RATTBE_LOGEVENT_TOOL_COMBO_FAILED.id)

        # Limits and offsets ONLY after all filters have been applied

        offset=0
        if format == "csv":
            # Ignore imits and offsets for CSV output
            pass
        else:
            if ('offset' in request.values):
                            offset=int(request.values['offset'])

            if ('limit' in request.values):
                    if request.values['limit']!="all":
                            limit=int(request.values['limit'])
                    else:
                            limit = 200

            if qt == 'normal':
                if limit>0:  q=q.limit(limit)
                if offset>0: q=q.offset(offset)

        if qt=='normal': dbq = q
        if qt=='count': count = q.count()
        


    def generate(fmt=None):
        fields=['datetime','user','member_id','email','tool','node','resource','event','doneby','message']
        if fmt == "csv":
            s = ""
            for f in fields:
                s += "\""+str(f)+"\","
            yield s+"\n"
        for l in dbq.all():
            r={}
            r['datetime']=l.time_logged.replace(tzinfo=utc).astimezone(eastern).replace(tzinfo=None)

            (r['when'],r['ago'],r['othertime'])=ago.ago(r['datetime'],now)

            if not l.member_id:
                    l.member_id=""
            elif l.member_id in members:
                r['user'] = ""
                if members[l.member_id]['last']:
                        r['user'] = members[l.member_id]['last']
                if members[l.member_id]['last']:
                        r['user'] +=", "+members[l.member_id]['first']
                if r['user'] == "":
                        r['user'] = members[l.member_id]['member']
                r['email']=members[l.member_id]['email']
                r['member_id']=members[l.member_id]['member']
            else:
                r['user']="Member #"+str(l.member_id)
            
            r['tool_id'] = l.tool_id
            if not l.tool_id:
                            r['tool'] = ""
            elif l.tool_id in tools:
                r['tool'] = tools[l.tool_id]
            else:
                r['tool']="Tool #"+str(l.tool_id)
            

            r['node_id']=l.node_id
            if not l.node_id:
                r['node']=""
            elif l.node_id in nodes:
                r['node'] = nodes[l.node_id]
            else:
                r['node']="Node #"+str(l.node_id)


            if not l.resource_id:
                r['resource']=""
            elif l.resource_id in resources:
                r['resource'] = resources[l.resource_id]
            else:
                r['resource']="Resource #"+str(l.resource_id)

            if (l.event_type in evt):
                r['event']=evt[l.event_type]
            else:
                r['event']=l.event_type

            if l.message:
                if (l.message.startswith("kioskimages:")):
                  r['message']="See Images"
                  r['extern_link']=url_for("logs.kioskentry",ke=l.message.replace("kioskimages:",""))
                else:
                  r['message']=l.message
            else:
                r['message']=""

            if not l.doneby:
                r['doneby'] = ""
                r['admin_id']=""
            elif l.doneby in members:
                if not members[l.doneby]['last']:
                    r['doneby'] = members[l.doneby]['member']
                else:
                    r['doneby'] = str(members[l.doneby]['last'])+", "+str(members[l.doneby]['first'])
                r['admin_id']=members[l.doneby]['member']
            else:
                r['doneby']="Member #"+str(l.doneby)
            if fmt == "csv":
                fields=['datetime','user','member_id','email','tool','node','resource','event','doneby','message']
                s = ""
                for f in fields:
                    if f in r:
                      s += "\""+str(r[f])+"\","
                    else:
                      s += "\"\","
                yield s+"\n"
            else:
                yield (r)


    if format == "html":
         logs = generate(fmt=format)
    elif format == "csv":
        resp=Response(generate(fmt=format),mimetype='text/csv')
        resp.headers['Content-Disposition']='attachment; filename=log.csv'
        return resp
    else:
        flash ("Invalid format requested","danger")
        return redirect(request.url);


    nextoffset = offset+limit
    if (offset >= count - limit):
        nextoffset=None
    else:
        if re.search("[\?\&]offset=(\d+)",request.url):
            nextoffset = re.sub(r"([\?\&])offset=(\d+)",r"\1offset="+str(nextoffset),request.url)
        else:
            if request.url.find("?")  == -1:
              nextoffset = request.url+"?offset="+str(nextoffset)
            else:
              nextoffset = request.url+"&offset="+str(nextoffset)

    prevoffset = offset-limit
    if (prevoffset < 0): prevoffset=0
    if offset <= 0:
      prevoffset = None
    else:
      if re.search("[\?\&]offset=(\d+)",request.url):
          prevoffset = re.sub(r"([\?\&])offset=(\d+)",r"\1offset="+str(prevoffset),request.url)
      else:
          if request.url.find("?")  == -1:
            prevoffset = request.url+"?offset="+str(prevoffset)
          else:
            prevoffset = request.url+"&offset="+str(prevoffset)

    if re.search("[\?\&]offset=(\d+)",request.url):
        firstoffset = re.sub(r"([\?\&])offset=(\d+)",r"",request.url)
    else:
        firstoffset = request.url

    lo = offset+limit
    if (lo > count):
        lo = count

    lastoffset = count-limit
    if (lastoffset < 0): lastoffset=0
    if re.search("[\?\&]offset=(\d+)",request.url):
        lastoffset = re.sub(r"([\?\&])offset=(\d+)",r"\1offset="+str(lastoffset),request.url)
    else:
        if request.url.find("?") != -1:
            lastoffset = request.url+"&offset="+str(lastoffset)
        else:
            lastoffset = request.url+"?offset="+str(lastoffset)

    if re.search("[\?\&]format=(\a+)",request.url):
        csvurl = re.sub(r"([\?\&])format=(\a+)",r"\1format=csv",request.url)
    else:
        if request.url.find("?") != -1:
            csvurl = request.url+"&format=csv"
        else:
            csvurl = request.url+"?format=csv"


    meta = {
            'offset':offset,
            'limit':limit,
            'first':firstoffset,
            'prev':prevoffset,
            'next':nextoffset,
            'last':lastoffset,
            'count':count,
            'csvurl':csvurl,
            'displayoffset':offset+1,
            'lastoffset':lo
    }
    if current_user.privs('Useredit','Finance','RATT'):
        meta['nomembersearch']=True
    else:
        meta['nomembersearch']=False


    fil_resources=Resource.query.all()
    fil_tools=Tool.query.all()
    fil_nodes=Node.query.all()
    return render_template('logs.html',logs=logs,resources=fil_resources,tools=fil_tools,nodes=fil_nodes,meta=meta)


@blueprint.route('/kiosk/<string:ke>')
def kioskentry(ke):
  ke = ke.replace("/","")
  ke = ke.replace(".","")
  imagecode=ke
  ke = ke.replace("kioskimages:","")
  if not current_user.is_arm() and (len(current_user.effective_roles()) == 0):
    flash("Not authorized for this page","warning")
    return redirect(url_for("index"))
  try:
    obj=json.load(open("authlibs/logs/static/kioskimages/"+imagecode+".json"))
    txt=obj['txt']
    res=obj['res']
  except:
    obj=None
    txt=""
    res=0
  if obj is None:
    try:
      cam_slackchan = current_app.config['globalConfig'].Config.get('cameras','slackchan')
      s = subprocess.Popen(['/var/www/covosk-cv/covid-mask-detector/testone.py',imagecode],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
      txt = s.stdout.read().strip()
      stderr = s.stderr.read().strip()
      if stderr and stderr != "":
          txt += "\nSTDERR: "+stderr
      res = s.wait()
      json.dump({'txt':txt,'res':res},open("authlibs/logs/static/kioskimages/"+imagecode+".json","w"))
    except BaseException as e:
      logger.error("Kiosk mask check error {0}".format(e))
      txt="BaseException:"+str(e)
  return render_template('kiosk_entry.html',entry=ke,txt=txt,res=res)
  
blueprint.route('/large.csv')
def generate_large_csv():
    def generate():
        for row in iter_all_rows():
            yield ','.join(row) + '\n'
    return Response(generate(), mimetype='text/csv')

@blueprint.route('/train/<string:ke>')
def kiosktrain(ke):
  ke = ke.replace("/","")
  ke = ke.replace(".","")
  imagecode=ke
  data={}
  try:
    data = json.load(open("authlibs/logs/static/kioskimages/{0}.irtrain".format(ke)))
  except:
    pass
  #print ("LOADED DATA",data)
  if 'save_good' in request.values:
    data['goodStartX'] = int(request.values['startX'])
    data['goodStartY'] = int(request.values['startY'])
    data['goodEndX'] = int(request.values['endX'])
    data['goodEndY'] = int(request.values['endY'])
    json.dump(data,open("authlibs/logs/static/kioskimages/{0}.irtrain".format(ke),"w"))
    return redirect(url_for("logs.kiosktrain",ke=ke))
  if 'save_bad' in request.values:
    data['badStartX'] = int(request.values['startX'])
    data['badStartY'] = int(request.values['startY'])
    data['badEndX'] = int(request.values['endX'])
    data['badEndY'] = int(request.values['endY'])
    json.dump(data,open("authlibs/logs/static/kioskimages/{0}.irtrain".format(ke),"w"))
    return redirect(url_for("logs.kiosktrain",ke=ke))
  if 'mark_invalid' in request.values:
    json.dump({},open("authlibs/logs/static/kioskimages/{0}.irtrain".format(ke),"w"))
    return redirect(url_for("logs.kiosktrain",ke=ke))
  g = glob.glob("authlibs/logs/static/kioskimages/*_ir.jpg")
  res=""
  if ke == "0000":
    ke = g[0].split("/")[-1].replace("_ir.jpg","")
  n=""
  p=""
  found_index="??"
  for (i,x) in enumerate(g):
    #print "COMPARE",x,ke
    if x == "authlibs/logs/static/kioskimages/{0}_ir.jpg".format(ke):
      #print ("FOUND")
      found_index=i
      try:
        p = g[i-1].split("/")[-1].replace("_ir.jpg","")
      except:
        pass
      try:
        n = g[i+1].split("/")[-1].replace("_ir.jpg","")
      except:
        pass
  txt = "Index "+str(found_index)+"\r\n"
  txt += ke
  drawcode=""
  if 'goodStartX' in data:
    drawcode += "dorect({0},{1},{2},{3},\"#ffffff80\");".format(
      data['goodStartX'],
      data['goodStartY'],
      data['goodEndX'],
      data['goodEndY'])
  if 'badStartX' in data:
    drawcode += "dorect({0},{1},{2},{3},\"#00000080\");".format(
      data['badStartX'],
      data['badStartY'],
      data['badEndX'],
      data['badEndY'])
  #txt +="\r\n"+str(g)
  #txt +="\r\n"+str(g)
  return render_template('kiosk_train.html',p=p,n=n,entry=ke,txt=txt,res=res,drawcode=drawcode)

def register_pages(app):
        app.register_blueprint(blueprint)
