// --------------------------------------------------------------------------
// libSkin.mel - MEL
Script
// --------------------------------------------------------------------------
//
// DESCRIPTION:
// This is a
nice
library
of
"skin"
procedures
to
help
those
that
// do
MEL
scripting.These
handle
things
for the skin deformer
// such as wrapping
skinCluster and skinPercent
commands.
//
// REQUIRES:
// Nothing.
//
//
// USAGE:
// source
"libSkin.mel";
//
//
// AUTHORS:
// Michael
B.Comet - comet @ comet - cartoons.com
// Copyright ?2004
Michael
B.Comet - All
Rights
Reserved.
//
// VERSIONS:
// 1.00 - Sep
8, 2004 - Initial
Release.
// 1.01 - Dec
1, 2004 - Added
add
inf
func.
// 1.02 - June
8, 2005 - Added
transfer
func.
//
// --------------------------------------------------------------------------

// --------------------------------------------------------------------------
// Library
Functions
// --------------------------------------------------------------------------

/ *
*libSkin_getSkinFromGeo() - Returns
the
names
of
any
skinClusters
*tied
to
the
history
of
passed in node.
* /
global proc
string[]
libSkin_getSkinFromGeo(string $geo)
{
    string $skins[];
clear $skins;

if ($geo == "" | | objExists($geo) != true)
return $skins;

string $hist[] = `listHistory - pdo
1 - il
2 $geo
`;
string $h;

for ($h in $hist)
    {
    if (nodeType($h) == "skinCluster")
    {
    $skins[size($skins)] = $h; // Store
    it
    }
    }

    return $skins;
}

// --------------------------------------------------------------------------

   / *
   * libSkin_getSkinsInScene() - Returns
all
skinClusters in scene
* /
global proc
string[]
libSkin_getSkinsInScene()
{
string $skins[];
clear $skins;

$skins = `ls - type
"skinCluster" "*"
`;

return $skins;
}

// --------------------------------------------------------------------------

   / *
   * libSkin_getGeoFromSkins() - For
each
skinCl
passed in, returns
related
geo
* /
global proc
string[]
libSkin_getGeoFromSkins(string $skins[])
{
string $geos[];
clear $geos;

int $i;
for ($i=0; $i < size($skins); ++$i)
{
if ($skins[$i] == "" | | objExists($skins[$i]) != true)
{
$geos[$i] = "";
continue;
}

string $shapes[] = `skinCluster - q - geometry $skins[$i]`;
string $xforms[] = `listRelatives - parent $shapes[0]
`;

$geos[$i] = $xforms[0];

}

return $geos;
}

// --------------------------------------------------------------------------

   / *
   * libSkin_getSkinGeosInScene() - Returns
all
geometry
that
has
a
skinCl in scene
* /
global proc
string[]
libSkin_getSkinGeosInScene()
{
string $geos[];
clear $geos;

string $skins[] = libSkin_getSkinsInScene();
$geos = libSkin_getGeoFromSkins( $skins );

return $geos;
}

// --------------------------------------------------------------------------

   / *
   * libSkin_getJointsFromSkin() - Returns
joints
from a skinCl
* /
global proc
string[]
libSkin_getJointsFromSkin(string $skin)
{
string $jnts[];
clear $jnts;

if ($skin == "" | | objExists($skin) != true)
return $jnts;

$jnts = `skinCluster - q - influence $skin
`;

return $jnts;
}

// --------------------------------------------------------------------------

   / *
   * libSkin_getWeight() - Returns
the
weight
given
a
skinCluster,
*	a joint we want the weight fo r, and the actual component. */
global proc float libSkin_getWeight(string $skin, string $jnt, string $comp)
{
float $wt = `skinPercent - t $jnt - q $skin $comp
`;
return $wt;
}

// --------------------------------------------------------------------------

   / *
   * libSkin_getAvgWeights() - Returns
the
average
weights
for the given
        * components and joint and skinCl.
        * /
global proc float libSkin_getAvgWeights(string $skin, string $jnt, string $comps[])
{
float $wt = 0.0;

int $nComp = size($comps);
if ($nComp <= 0)
    return 0.0;

string $c;
for ($c in $comps)
    {
    $wt += libSkin_getWeight($skin, $jnt, $c);
    }

    $wt = $wt / $nComp; // Average
    it!

    return $wt;
}

// --------------------------------------------------------------------------

   / *
   * libSkin_setWeight() - Sets
the
weight
given
a
skinCluster,
*	a joint we want the weight fo r, and the actual component. */
global proc libSkin_setWeight(string $skin, string $jnt, string $comp, float $val)
{
skinPercent - tv $jnt $val $skin $comp;
}

// --------------------------------------------------------------------------

   / *
   * libSkin_isLocked() - Returns
0 or 1 if the
related
jnt is locked / held
*
for skining.
    * /
global proc int libSkin_isLocked(string $skin, string $jnt)
{
int $lock = `skinCluster - inf $jnt - q - lockWeights $skin
`;
return $lock;
}

// --------------------------------------------------------------------------

   / *
   * libSkin_setLock() - Sets
a
HOLD / Lock
weight
* /
global proc
libSkin_setLock(string $skin, string $jnt, int $lock)
{
skinCluster - inf $jnt - e - lockWeights $lock $skin;
}

// --------------------------------------------------------------------------

   / *
   * libSkin_toggleLock() - Togles
a
HOLD / Lock
weight
* /
global proc
libSkin_toggleLock(string $skin, string $jnt)
{
int $lock = libSkin_isLocked($skin, $jnt);
$lock = 1 - $lock;
libSkin_setLock($skin, $jnt, $lock);
}

// --------------------------------------------------------------------------

   / *
   * libSkin_getCompsFromJoints() - Given
a
skinCl and some
joints in it,
* return any
components
that
have
a
non - zero
weight
for those joints / cluster.
    * /
    global proc
    string[]
    libSkin_getCompsFromJoints(string $skin, string $jnts[])
    {
        string $comps[];
    clear $comps;

    string $shapes[] = `skinCluster - q - geometry $skin
    `;
    string $shape = $shapes[0];

    // Select
    all
    comps as a
    start
    to
    determine
    how
    many
    etc....
    if (nodeType($shape) == "nurbsSurface" | | nodeType($shape) == "nurbsCurve")
    select - r($shape + ".cv[*]");
    else if (nodeType($shape) == "mesh")
    select -r ($shape+".vtx[*]");
    else if (nodeType($shape) == "subdiv")
    select -r ($shape+".smp[*]");
    else if (nodeType($shape) == "lattice")
    select -r ($shape+".pt[*]");
    else
    return $comps;

    // So
    what
    are
    all
    the
    components?
    string $allComps[] = `ls - sl - flatten`;
    select - cl;

    // What
    joints
    are
    used?
    string $skinJnts[] = `skinCluster - q - influence $skin
    `;

    string $c;
    for ($c in $allComps)
        {
        // What is the
        weight
        of
        the
        current
        component
        for all transforms?
        float $wts[] = `skinPercent -q -v $skin $c`;

        // For each non zero weight...
        int $w;
        for ($w=0; $w < size($wts); ++$w)
        {
        if ($wts[$w] > 0.0)
        {
        // If it is non zero, then see if it is one of the joints we want..
        int $idx = -1;
        int $j;
        for ($j=0; $j < size($jnts); ++$j)
        {
        if ($jnts[$j] == $skinJnts[$w])
        {
        $idx = $j;
        break;
        }
        }
        if ($idx >= 0) // So if it is a joint we want, add this cv
        {
        $comps[size($comps)] = $c;
    break;
    }

    } // end
    of if wt > 0

    } // end
    of
    each
    wt

    } // end
    of
    sel

    return $comps;
    }

    // --------------------------------------------------------------------------

       / *
       * libSkin_getJointsFromComps() - Given
    a
    skinCluster and some
    components,
    *	figure out what joints are affecting these c
    v's with a non zero wt. */
global proc string[] libSkin_getJointsFromComps(string $skin, string $comps[])
{
string $jnts[] ;
clear $jnts ;


// G
    t all joints used in
    skin cluster...
string $skinJnts[] = `skinCluster -q -inf
    u
    nce $skin` ;str
    ng $c;
for ($c

    in $
    com
    s)
    {
    // Get wei
    hts for th
    s component...
            float $w ts[ ] = `skinPercen
    t-q

    -v $skin $
    c` ;

    // Now for
        each non zero
        weight..
        .
    int $w ;
    for ($w=0 ; $w < size($wts); ++$w)
    {
    if ($wts[$w]> 0.0)
    {
    // If it is non zero, then
        addthe
        joint wih this index to the list
        // if
        it hasn't been
         yet.
    int $idx = -1 ;
    int $j ;
    for ($j=0; $j < size($jnts); ++$j)
    {
    if ($jnts[$j] == $skinJnts[
        $w]){
    $idx = $j ;
        break ;
    }
    }
    if ($idx == -1)  // If still -1, then we haven't seen
        et!
    {
    $jnts[
        sze($
        jnts)] = $
        skinJnts[$w] ;
    }

    }  // end of if wt > 0

    } // end
        of
        each wt

    } // end of selreturn $

        jnts ; }



// -----------------

        -------------------

        ------------

    ------------

    ---

    -----------

   /*
   * libSkin_getSelComps() - Returns a list of obj.comp[]

       for any selected components
*		that
    ma
    ch t
    e
    current skin cluster...
*/
global proc
    st ng[] libSkin_getSelComps(string $skin)
    {
    string $sel[] = `ls -sl -fl`;
int $nSel = size($sel) ;
    if
    ($skin == "" || objEx ists ($sk
    n) != true)
return {} ;

    // Get things that look like components only..
    ie: has a .

    dot in it.
s
    ring
    $com
    s[] ;
clear $co
    ps ;
int $nCo
    p=0 ;

int $i ;
for ($i=0; $i < $nSel; ++$i)
    {
    // Dos

    it have a . ?
    if (gmatch($sel[$i],
        "*.*"
        )
        == 1
        ){
    // If
        so, also make sure it is related
        to
        this skinCluster.
    string $skins[] = libSkin_getSkin
        eo($sel[$i]) ;
    if ($skins[0] == $skin)
    {
    $
        comps[$nComp] = $sel[$i] ;
    +
        +$nComp ;
    } // sme
        skinCl

    }
        // matches a .

        comp

    }//Each sel

        item

return $

    comps ;
}

//--
    --

    ----------------------------------------------------------------------

   /* * lib
       _addInfluences() - Adds influenc
    s to a node
    .
                                                    */
    global proc libSkin
    a
    dInfluences(string $skin, string $infs[])
{
string $ jnts[] = libSkin_getJoints
    romSkin($

    skin) ;	//W
    at is currently in the
        skinCl
            ?
        string $inf ;
for ($inf in $infs)
    {
        string $j;
    int $exists
        = \
        0 ;
    for (
        $j in
        $
        jnts)
    {
    if ( $inf == $j)
    {
    $exists = 1;
    bre
    k ;
    }
    }
    if ($ exi sts
    )	 //
    If alre ady a pa rt of the clut r, ignore
    .
    con
    in
    e ;

sk
    nCluster -e -dr 16 -lw t
    ue -wt 0.0 -a i $ inf $skin ;	// First addit to clus
    er with a
    lock we
    ght of 0.

        skinCluster -e -lw false -inf $inf $skin ;	// Then unlock the weight for it.
    }

}

// ---

           -
           --------------------------------
        ----------
        --
        -
        -------------- --
        ---------

   /*
   *
        libSkin_removeInfluences() - Adds i
        f
            es to a node.
                                                       */
global
        proc libS

        n_removeInfu
        nces(string $skin,
        st
    ing $infs[]
    )
{
    string$
    jnts[] = libSkin_
        i
        omSkin($skin) ;	//
        What is currently in the skinl ?
        string $inf ;
        for ($inf in $infs)
{
string $j;
int $exists = 0 ;
    for ($jin $

    jnts)
    {
    if ($inf ==$j )
    {
    $
    exists = 1 \
    ;
    break ;
    }

    }

    if (!$exists)		// If not a part of the cluster, ignore.
continue ;

skinCluster -e -

       ri $inf $skin ;	// Remove this influence
    from t
    e skinCl
    ster.
}

}

    // ---
    --
    ---------------------------------------------------------------------

   /*
   * li
    Skin_transf
    rWeight() - Transfers weight from all from jnts to the to jnt
                                                                              */
global proc libS
    in_tras
    erWeight(string $s kin, string $jntsFrom[], str
    ng $jnTo
    , string $comps[ ] )
{
    int $nComp = size(
    $comps)

    ;
int $i ; if (size($jntsFrom) <= 0)re n ;
if (
    $j
    tTo == ""
    || o

    Exists
    ($j
    tTo)
    != tr
    e)
return ;
if ($skin == "" ||
        objExists
            ($skin) != true)
return ;
        setAttr ($ski n+".normalizeWeights") 0 ;			//Turn off Norm
        lize
        now!

//
        Go thru each
        point
for ($i=0; $i
        < $nComp; ++$i)
    {
        int
        $nPct = 100 * $i / ($nComp-1) ;
    print ("// "+$nPct+"  "+$comps[$i]+" //\n") ;

    // Go thru each
        jntfor this pt
    string $jntFrom ;
    for ($jntFrom in $jntsFrom)
    {
    f
        oat $wt
        = libS
        in

        ight($skin, $jntFrom, $comps[$i] ) ; 	// Get currentw t
        if ($wt == 0
        0)
    continue ;

    float $wtTo = libSkin_getWeight($ skin,$ jntTo,
        $co
        ps[
        $i] ) ; 	//
        Get current


        weiht To

    libSkin_setWeight($ skin, $
        jntFrom, $com
        s[$i], 0.0 ) ; 			// Set orig to 0
    libSkin_setWeight($skin, $jntTo, $comps[$i], $wtTo+$wt) ; 		// Add wts to new one

    }
    }


    setAttr ($skin+".normalizeWeights") 1 ;			// Turn on! Normalize now!

    }

    // --------------------------------------------------------------------------







